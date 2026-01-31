"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Edit2, Trash2, Save, X, Plus, User } from "lucide-react";
import type { Character } from "@/types";

interface CharacterCardProps {
  character: Character;
  index: number;
  onEdit?: (character: Character) => void;
  onDelete?: () => void;
  locale?: "en" | "zh";
}

export function CharacterCard({
  character,
  index,
  onEdit,
  onDelete,
  locale = "zh",
}: CharacterCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(character);

  // Localized labels
  const editCharacterLabel = locale === "zh" ? "编辑角色" : "Edit Character";
  const nameLabel = locale === "zh" ? "姓名" : "Name";
  const ageLabel = locale === "zh" ? "年龄" : "Age";
  const personalityLabel = locale === "zh" ? "性格" : "Personality";
  const appearanceLabel = locale === "zh" ? "外貌" : "Appearance";
  const visualDescLabel = locale === "zh" ? "视觉描述" : "Visual Description";
  const majorEventsLabel = locale === "zh" ? "重大经历" : "Major Events";
  const saveLabel = locale === "zh" ? "保存" : "Save";
  const cancelLabel = locale === "zh" ? "取消" : "Cancel";

  const handleSave = () => {
    onEdit?.(editData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData(character);
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <User className="w-4 h-4" />
            {editCharacterLabel} {index + 1}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>{nameLabel}</Label>
              <Input
                value={editData.name}
                onChange={(e) =>
                  setEditData({ ...editData, name: e.target.value })
                }
              />
            </div>
            <div className="space-y-2">
              <Label>{ageLabel}</Label>
              <Input
                value={editData.age || ""}
                onChange={(e) =>
                  setEditData({ ...editData, age: e.target.value })
                }
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>{personalityLabel}</Label>
            <Textarea
              value={editData.personality}
              onChange={(e) =>
                setEditData({ ...editData, personality: e.target.value })
              }
              rows={2}
            />
          </div>

          <div className="space-y-2">
            <Label>{appearanceLabel}</Label>
            <Textarea
              value={editData.appearance}
              onChange={(e) =>
                setEditData({ ...editData, appearance: e.target.value })
              }
              rows={2}
            />
          </div>

          <div className="space-y-2">
            <Label>{visualDescLabel}</Label>
            <Textarea
              value={editData.visual_description}
              onChange={(e) =>
                setEditData({ ...editData, visual_description: e.target.value })
              }
              rows={2}
            />
          </div>

          <div className="flex gap-2">
            <Button onClick={handleSave} size="sm">
              <Save className="w-4 h-4 mr-1" />
              {saveLabel}
            </Button>
            <Button variant="outline" onClick={handleCancel} size="sm">
              <X className="w-4 h-4 mr-1" />
              {cancelLabel}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <User className="w-4 h-4" />
            {character.name}
          </CardTitle>
          <div className="flex items-center gap-1">
            {character.age && (
              <Badge variant="secondary">{character.age}</Badge>
            )}
            {onEdit && (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => setIsEditing(true)}
              >
                <Edit2 className="w-4 h-4" />
              </Button>
            )}
            {onDelete && (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-red-500 hover:text-red-600"
                onClick={onDelete}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div>
          <span className="font-medium text-zinc-500">{personalityLabel}: </span>
          {character.personality}
        </div>
        <div>
          <span className="font-medium text-zinc-500">{appearanceLabel}: </span>
          {character.appearance}
        </div>
        {character.visual_description && (
          <div>
            <span className="font-medium text-zinc-500">{visualDescLabel}: </span>
            {character.visual_description}
          </div>
        )}
        {character.major_events && character.major_events.length > 0 && (
          <div>
            <span className="font-medium text-zinc-500">{majorEventsLabel}:</span>
            <ul className="list-disc list-inside mt-1 text-zinc-600 dark:text-zinc-400">
              {character.major_events.map((event, i) => (
                <li key={i}>{event}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface CharacterListProps {
  characters: Character[];
  onUpdate?: (index: number, character: Character) => void;
  onDelete?: (index: number) => void;
  onAdd?: (character: Character) => void;
  locale?: "en" | "zh";
}

export function CharacterList({
  characters,
  onUpdate,
  onDelete,
  onAdd,
  locale = "zh",
}: CharacterListProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newCharacter, setNewCharacter] = useState<Character>({
    name: "",
    personality: "",
    appearance: "",
    visual_description: "",
  });

  // Localized labels
  const addNewCharLabel = locale === "zh" ? "添加新角色" : "Add New Character";
  const nameLabel = locale === "zh" ? "姓名" : "Name";
  const ageLabel = locale === "zh" ? "年龄" : "Age";
  const personalityLabel = locale === "zh" ? "性格" : "Personality";
  const appearanceLabel = locale === "zh" ? "外貌" : "Appearance";
  const namePlaceholder = locale === "zh" ? "角色姓名" : "Character name";
  const agePlaceholder = locale === "zh" ? "年龄" : "Age";
  const personalityPlaceholder = locale === "zh" ? "描述角色性格..." : "Describe personality...";
  const appearancePlaceholder = locale === "zh" ? "描述角色外貌..." : "Describe appearance...";
  const addLabel = locale === "zh" ? "添加" : "Add";
  const cancelLabel = locale === "zh" ? "取消" : "Cancel";
  const addCharacterLabel = locale === "zh" ? "添加角色" : "Add Character";

  const handleAdd = () => {
    if (newCharacter.name && newCharacter.personality) {
      onAdd?.(newCharacter);
      setNewCharacter({
        name: "",
        personality: "",
        appearance: "",
        visual_description: "",
      });
      setShowAddForm(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        {characters.map((character, index) => (
          <CharacterCard
            key={index}
            character={character}
            index={index}
            onEdit={onUpdate ? (c) => onUpdate(index, c) : undefined}
            onDelete={onDelete ? () => onDelete(index) : undefined}
            locale={locale}
          />
        ))}
      </div>

      {onAdd && (
        <>
          {showAddForm ? (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">{addNewCharLabel}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>{nameLabel} *</Label>
                    <Input
                      value={newCharacter.name}
                      onChange={(e) =>
                        setNewCharacter({ ...newCharacter, name: e.target.value })
                      }
                      placeholder={namePlaceholder}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{ageLabel}</Label>
                    <Input
                      value={newCharacter.age || ""}
                      onChange={(e) =>
                        setNewCharacter({ ...newCharacter, age: e.target.value })
                      }
                      placeholder={agePlaceholder}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>{personalityLabel} *</Label>
                  <Textarea
                    value={newCharacter.personality}
                    onChange={(e) =>
                      setNewCharacter({
                        ...newCharacter,
                        personality: e.target.value,
                      })
                    }
                    placeholder={personalityPlaceholder}
                    rows={2}
                  />
                </div>

                <div className="space-y-2">
                  <Label>{appearanceLabel}</Label>
                  <Textarea
                    value={newCharacter.appearance}
                    onChange={(e) =>
                      setNewCharacter({
                        ...newCharacter,
                        appearance: e.target.value,
                      })
                    }
                    placeholder={appearancePlaceholder}
                    rows={2}
                  />
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleAdd} size="sm">
                    <Plus className="w-4 h-4 mr-1" />
                    {addLabel}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowAddForm(false)}
                    size="sm"
                  >
                    {cancelLabel}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Button
              variant="outline"
              onClick={() => setShowAddForm(true)}
              className="w-full"
            >
              <Plus className="w-4 h-4 mr-1" />
              {addCharacterLabel}
            </Button>
          )}
        </>
      )}
    </div>
  );
}
